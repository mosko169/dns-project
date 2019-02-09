import dns.resolver
import csv
import traceback
import argparse


NS_QUERY = "NS"


class AAnswer:
    def __init__(self, name, ip_addr):
        self.name = name
        self.ip_addr = ip_addr

    def __str__(self):
        return "name: " + self.name + " ip: " + self.ip_addr


class NSAnswer:
    def __init__(self, domain, name_servers, glue_records, out_of_bailiwick_glue_records):
        self.domain = domain
        self.name_servers = name_servers
        self.glue_records = glue_records
        self.out_of_bailiwick_glue_records = out_of_bailiwick_glue_records

    def __str__(self):
        answer_str = "domain: " + self.domain
        answer_str += "\nname servers: \n"
        answer_str += '\n'.join(self.name_servers)
        answer_str += "\nglue records: \n"
        answer_str+= '\n'.join([str(glue_record) for glue_record in self.glue_records])
        answer_str += "\nout of bailiwick glue records: \n"
        answer_str+= '\n'.join([str(out_of_bailiwick_glue_record) for out_of_bailiwick_glue_record in self.out_of_bailiwick_glue_records])
        return answer_str


def strip_trailing_dot(name):
    if name.endswith('.'):
        name = name[:-1]
    return name


def parse_a_record(a_record):
    name = strip_trailing_dot(a_record.name.to_text())
    ipAddr = a_record.items[0].to_text()
    return AAnswer(name, ipAddr)


def out_of_bailiwick_domain(original_domain, subdomain):
    return not subdomain.name.endswith(original_domain)


def parse_answer(domain, answer):
    name_servers = [strip_trailing_dot(entry.to_text()) for entry in answer]
    glue_records = [parse_a_record(a_record) for a_record in answer.response.additional]
    out_of_bailiwick_glue_records = [glue_record for glue_record in glue_records if out_of_bailiwick_domain(domain, glue_record)]
    return NSAnswer(domain, name_servers, glue_records, out_of_bailiwick_glue_records)


def query_domains(domains):
    print("querying " + str(len(domains)) + " domains")
    resolver = dns.resolver.Resolver()
    # use this when running from resolver
    #resolver.nameservers = ["127.0.0.1"]
    answers = []
    for index, domain in enumerate(domains):
        try:
            answer = resolver.query(domain, NS_QUERY)
            answers.append(parse_answer(domain, answer))
        except Exception as e:
            traceback.print_exc()
            print("FAILED TO QUERY DOMAIN " + domain + " ERROR: " + str(e))
        print("queried " + str(index + 1) + " / " + str(len(domains)) + " domains")

    return answers

def parse_domains_file(file_path):
    domains = []
    with open(file_path, "r", encoding='UTF-8') as domains_file:
        next(domains_file)
        reader = csv.reader(domains_file)
        for domain_entry in reader:
            try:
                domains.append(domain_entry[2])
            except Exception as e:
                continue
    return domains


def dump_stats(answers, output_path):
    with open(output_path, mode='w', newline='') as csv_file:
        fieldnames = ['domain_name', 'name_servers_count', 'glue_records_count', 'out_of_bailiwick_glue_records']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for answer in answers:
            writer.writerow({'domain_name': answer.domain,
                             'name_servers_count': len(answer.name_servers),
                             'glue_records_count': len(answer.glue_records),
                             'out_of_bailiwick_glue_records': len(answer.out_of_bailiwick_glue_records)})


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
    """
     TODO
     CDF name_servers_count
     CDF glue_records_count
     CDF out_of_bailiwick_glue_records
     histogram of name_servers_count
    """

    dump_stats(answers, args.output_path)


if __name__ == '__main__':
    main()
