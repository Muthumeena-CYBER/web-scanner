# Main runner
from crawler import crawl_site
from detector import test_sqli
from colorama import Fore, Style, init
import sys
from xss_detector import test_xss
from csrf_detector import test_csrf

init(autoreset=True)

def main():
    if len(sys.argv) != 2:
        print("Usage: python scanner.py <target_url>")
        sys.exit(1)

    target = sys.argv[1]
    print(Fore.CYAN + f"[+] Crawling target: {target}")
    print(Fore.CYAN + f"[+] Generating sitemap...")

    urls = crawl_site(target)
    print(Fore.GREEN + f"[✓] Sitemap generated successfully")
    print(Fore.CYAN + f"[+] Found {len(urls)} URLs\n")

    vulnerable = False

    for url in urls:
        findings = test_sqli(url)
        if findings:
            vulnerable = True
            print(Fore.RED + f"[!] SQL Injection Found: {url}")
            for param, payload, sqli_type in findings:
                print(
                    Fore.YELLOW +
                    f"    ├─ Parameter: {param}\n"
                    f"    ├─ Payload: {payload}\n"
                    f"    └─ Type: {sqli_type}\n"
                )

        # XSS scan
        xss_findings = test_xss(url)
        if xss_findings:
            vulnerable = True
            print(Fore.RED + f"[!] XSS Found: {url}")
            for param, payload, xss_type in xss_findings:
                print(
                    Fore.YELLOW +
                    f"    ├─ Parameter: {param}\n"
                    f"    ├─ Payload: {payload}\n"
                    f"    └─ Type: {xss_type}\n"
                )

        # CSRF scan
        csrf_findings = test_csrf(url, urls)
        if csrf_findings:
            vulnerable = True
            print(Fore.RED + f"[!] CSRF Vulnerability Found: {url}")
            for form_name, vuln_type, severity, details in csrf_findings:
                print(
                    Fore.YELLOW +
                    f"    ├─ Form/Component: {form_name}\n"
                    f"    ├─ Vulnerability Type: {vuln_type}\n"
                    f"    ├─ Severity: {severity}\n"
                    f"    └─ Details: {details}\n"
                )

    if not vulnerable:
        print(Fore.GREEN + "[✓] No SQL Injection, XSS, or CSRF vulnerabilities found.")

if __name__ == "__main__":
    main()


