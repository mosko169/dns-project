import dns.resolver
import csv
import argparse
import threading


NS_QUERY = "NS"
THREADS = 20


class AAnswer:
    def __init__(self, name, ip_addr):
        self.name = name
        self.ip_addr = ip_addr

    def __str__(self):
        return "name: " + self.name + " ip: " + self.ip_addr


class NSAnswer:
    def __init__(self, domain, name_servers, glue_records_v4, glue_records_v6, out_of_bailiwick_glue_records_v4, out_of_bailiwick_glue_records_v6):
        self.domain = domain
        self.name_servers = name_servers
        self.glue_records_v4 = glue_records_v4
        self.glue_records_v6 = glue_records_v6
        self.out_of_bailiwick_glue_records_v4 = out_of_bailiwick_glue_records_v4
        self.out_of_bailiwick_glue_records_v6 = out_of_bailiwick_glue_records_v6

    def __str__(self):
        answer_str = "domain: " + self.domain
        answer_str += "\nname servers: \n"
        answer_str += '\n'.join(self.name_servers)
        answer_str += "\nglue records: \n"
        answer_str+= '\n'.join([str(glue_record) for glue_record in self.glue_records_v4])
        answer_str += "\nout of bailiwick glue records: \n"
        answer_str+= '\n'.join([str(out_of_bailiwick_glue_record) for out_of_bailiwick_glue_record in self.out_of_bailiwick_glue_records])
        return answer_str


def get_chunks(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def strip_trailing_dot(name):
    if name.endswith('.'):
        name = name[:-1]
    return name


def parse_a_record(a_record):
    name = strip_trailing_dot(a_record.name.to_text())
    ipAddr = a_record.items[0].to_text()
    return AAnswer(name, ipAddr)


def out_of_bailiwick_domain(original_domain, name_server):
    """
    checks whether a name server is in-bailiwick of a domain by validating
    that their suffix is the same
    :param original_domain: domain which to check its name server
    :param name_server: name server to check
    """
    return not name_server.name.endswith(original_domain)


def parse_answer(domain, answer):
    name_servers = [strip_trailing_dot(entry.to_text()) for entry in answer]
    glue_records_ipv4 = [parse_a_record(a_record) for a_record in answer.response.additional if a_record.rdtype == 1]
    glue_records_ipv6 = [parse_a_record(a_record) for a_record in answer.response.additional if a_record.rdtype == 28]
    out_of_bailiwick_glue_records_v4 = [glue_record for glue_record in glue_records_ipv4 if out_of_bailiwick_domain(domain, glue_record)]
    out_of_bailiwick_glue_records_v6 = [glue_record for glue_record in glue_records_ipv6 if out_of_bailiwick_domain(domain, glue_record)]
    return NSAnswer(domain,
                    name_servers,
                    glue_records_ipv4,
                    glue_records_ipv6,
                    out_of_bailiwick_glue_records_v4,
                    out_of_bailiwick_glue_records_v6)


def query_worker(domains, results, chunk_index):
    """
    queries given domains for NS records and parses the answers
    :param domains: domains to query
    :param results: results vector to fill
    :param chunk_index: index of domains chunk
    """
    resolver = dns.resolver.Resolver()
    # use this when running from resolver
    #resolver.nameservers = ["127.0.0.1"]
    for index, domain in enumerate(domains):
        try:
            answer = resolver.query(domain, NS_QUERY)
            results.append(parse_answer(domain, answer))
        except Exception as e:
            print("FAILED TO QUERY DOMAIN " + domain + " ERROR: " + str(e))
        print("CHUNK " + str(chunk_index) + " queried " + str(index + 1) + " / " + str(len(domains)) + " domains")


def query_domains(domains):
    """
    perform NS queries for the given domains
    :param domains: domains to query
    """
    print("querying " + str(len(domains)) + " domains")
    chunks = get_chunks(domains[:1], THREADS)
    resolve_threads = []
    answers_list = []
    for index, chunk in enumerate(chunks):
        answers = []
        answers_list.append(answers)
        resolve_thread = threading.Thread(target=query_worker, args=[chunk, answers, index])
        resolve_thread.start()
        resolve_threads.append(resolve_thread)

    for t in resolve_threads:
        t.join()
    return [answer for answers in answers_list for answer in answers]


def parse_domains_file(file_path):
    domains = []
    with open(file_path, "r", encoding='UTF-8') as domains_file:
        next(domains_file)
        reader = csv.reader(domains_file)
        for domain_entry in reader:
            try:
                domains.append(domain_entry[2])
            except Exception as e:
                # could not read domain, just skip
                continue
    return domains


def dump_stats(answers, output_path):
    with open(output_path, mode='w', newline='') as csv_file:
        fieldnames = ['domain_name',
                      'name_servers_count',
                      'ipv4_glue_records_count',
                      'ipv4_out_of_bailiwick_glue_records',
                      'ipv6_glue_records_count',
                      'ipv6_out_of_bailiwick_glue_records']

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for answer in answers:
            writer.writerow({'domain_name': answer.domain,
                             'name_servers_count': len(answer.name_servers),
                             'ipv4_glue_records_count': len(answer.glue_records_v4),
                             'ipv4_out_of_bailiwick_glue_records': len(answer.out_of_bailiwick_glue_records_v4),
                             'ipv6_glue_records_count': len(answer.glue_records_v6),
                             'ipv6_out_of_bailiwick_glue_records': len(answer.out_of_bailiwick_glue_records_v6)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domains_file_path", help="path of domains file retrieved from https://majestic.com/reports/majestic-million", required=False)
    parser.add_argument("-domains", help="a list of domains to perform queries on", nargs='+', required=False)
    parser.add_argument("-output_path", help="path to write statistics to", required=True)
    args = parser.parse_args()
    domains = args.domains
    domains_file_path = args.domains_file_path
    if not (domains or domains_file_path):
        parser.print_help()
        exit(0)

    domains_to_query = []
    if domains_file_path:
        domains_to_query += parse_domains_file(domains_file_path)
    if domains:
        domains_to_query += domains

    answers = query_domains(domains_to_query)
    dump_stats(answers, args.output_path)


if __name__ == '__main__':
    main()
