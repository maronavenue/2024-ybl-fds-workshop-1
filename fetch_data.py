import csv
import datetime
import json
import re
import requests


def extract_sector_and_subsector(input_string: str) -> (str, str):
    sector, subsector = input_string.split("|")
    return sector, subsector


def extract_date(input_string: str) -> int:
    converted_date = datetime.datetime.strptime(input_string, "%d/%m/%Y").strftime("%Y%m%d")
    return converted_date


def extract_currency(input_string: str) -> (str, float):
    result = re.search(r"([A-Z]{3})(\-?\d+\.?\d{2})", input_string)
    return result.group(1), float(result.group(2))


def convert_usd_to_target(usd_value: float, target_currency: str) -> float:
    response = requests.get("https://openexchangerates.org/api/latest.json?app_id=93c5a36e15f84af2abcbd6d0f97d9b20&base=USD")
    data = response.json()
    exrate = data['rates'][target_currency]
    result = usd_value * exrate
    return result


def main():

    data = {}
    
    with open('pse_data_01052024.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        for index, row in enumerate(reader):
            if index == 0:
                continue
            if row[0].startswith("<"):
                continue
            key = row[0]
            raw_date = row[1]
            company_name = row[2]
            company_price = row[3]
            company_shares = float(row[4])
            net_foreign = row[5]
            sector_subsector = row[6]

            if key not in data:
                data[key] = {}
            data[key]["NAME"] = company_name
            data[key]["SECTOR"], data[key]["SUBSECTOR"] = extract_sector_and_subsector(sector_subsector)

            date = extract_date(raw_date)
            if date not in data[key]:
                data[key][date] = {}
    
            currency, price_data = extract_currency(company_price)
            if currency == 'USD':
                price_data = convert_usd_to_target(price_data, 'PHP')
            data[key][date]["PRICE"] = round(price_data, 2)
            data[key][date]["SHARES"] = round(company_shares, 2)
            currency, net_foreign_data = extract_currency(net_foreign)
            if currency == 'USD':
                net_foreign_data = convert_usd_to_target(net_foreign_data, 'PHP')
            data[key][date]["NET_FOREIGN"] = round(net_foreign_data, 2)
            mcap = price_data * company_shares
            data[key][date]["MCAP"] = mcap
    
    print(json.dumps(data, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()