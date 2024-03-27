import ezgmail

unreadThreads = ezgmail.unread(maxResults=300)
print(f'There are {len(unreadThreads)} unread emails in your account')

for unread in unreadThreads:
    print(ezgmail.summary(unread), '\n')
    # unread.markAsRead()