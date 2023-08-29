import requests
import time
import math

# insert api token
api_token = ""


# called in _get_user_data. Returns all pages that a user follows
def _get_user_subscriptions(user_id):
    try:
        # The VK api returns 1000 results a time so we need to make multiple requests to collect all data
        amount_of_followed_pages = _get_followed_pages_amount(user_id)

        if amount_of_followed_pages <= 1000:
            params = (
                ('access_token', api_token),
                ('v', '5.65'),
                ('count', '1000'),
                ('user_id', '{0}'.format(user_id)),
            )
            response = requests.get('https://api.vk.com/method/groups.get', params=params)

            response = response.json()
            subscriptions = response["response"]["items"]
            return subscriptions

        else:
            subscriptions = []
            # calculate the amount of required requests
            needed_requests = math.ceil(amount_of_followed_pages / 1000)
            offset = 0
            for i in range(0, needed_requests):
                if i % 3 == 0:
                    time.sleep(1)

                params = (
                    ('access_token', api_token),
                    ('v', '5.65'),
                    ('count', '1000'),
                    ('offset', '{0}'.format(offset)),
                    ('user_id', '{0}'.format(user_id)),
                )
                response = requests.get('https://api.vk.com/method/groups.get', params=params)

                response = response.json()
                subscriptions += response["response"]["items"]

                offset += 1000

            return subscriptions

    # if a user has a private page or doesnt allow us to view his subscriptions we raise a KeyError
    # Which is handled in _get_user_data()
    except KeyError:
        raise KeyError


# supporting function for _get_user_subscriptions()
# returns Int amount of followed pages for a user
def _get_followed_pages_amount(user_id):
    params = (
        ('access_token', api_token),
        ('v', '5.65'),
        ('user_id', '{0}'.format(user_id)),
    )

    response = requests.get('https://api.vk.com/method/groups.get', params=params)
    response = response.json()
    return response["response"]["count"]


# supporting function for _get_members_list()
# returns Int amount of page followers
def _get_subscriber_amount(community_name):
    params = (
        ('access_token', api_token),
        ('v', '5.65'),
        ('group_id', '{0}'.format(community_name)),
        ('fields', 'members_count'),
    )

    response = requests.get('https://api.vk.com/method/groups.getById', params=params)
    response = response.json()

    return response["response"][0]["members_count"]


# gathers all  subscriptions for all page members and puts them into a dictionary
def _get_user_data(members):
    data_dict = {

    }

    for i in range(0, len(members)):
        if i % 3 == 0:
            time.sleep(1)
        try:
            subscriptions = ','.join(map(str, _get_user_subscriptions(members[i])))
            # the key is the user id and the value are his subscriptions
            data_dict[members[i]] = subscriptions
        except KeyError:
            pass

    return data_dict


# Main function. Gets all members for a community and finds all followed pages for each member
def main_call(community_name):
    members = _get_members_list(community_name)
    print("gathered members.")
    data = _get_user_data(members)
    print("finished gathering all data.")

    # after all data is collected we write this data to a CSV file
    with open('data.csv', 'w') as f:
        for key in data.keys():
            f.write("%s,%s\n" % (key, data[key]))


# We get 1000 results at a time from the VK API
# So we calculate the amount of needed requests and increase the query offset each time
def _get_members_list(community_name):
    members = []
    amount_of_subscribers = _get_subscriber_amount(community_name)
    needed_requests = math.ceil(amount_of_subscribers / 1000)
    offset = 0

    for i in range(0, needed_requests):
        if i % 3 == 0:
            time.sleep(1)

        params = (
            ('access_token', api_token),
            ('v', '5.65'),
            ('count', '1000'),
            ('offset', '{0}'.format(offset)),
            ('group_id', '{0}'.format(community_name)),

        )

        response = requests.get('https://api.vk.com/method/groups.getMembers', params=params)

        response = response.json()
        members += response["response"]["items"]

        offset += 1000

    return members


# Function call + execution timer
t0 = time.time()

# insert any community name here
main_call("")
t1 = time.time()

total = t1-t0
print("All data collected and written to CSV file. It to took: {0} seconds".format(total))
