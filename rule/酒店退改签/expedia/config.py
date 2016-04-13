sip = '10.136.55.156'
sip = '10.136.1.121'
spwd = 'miaoji1109'
sip = '127.0.0.1'
spwd = ''
suser = 'root'
sourcedb='onlinedb'
dip = '127.0.0.1'##################self_ip
duser = 'root'
dpwd = ''

#redis
rip = '127.0.0.1'
rpwd = 'MiojiRedisOrz'
day_dept=130
mail_list='yuanjingwei@mioji.com'#;dengzhilong@mioji.com'

#data from parser mysql configure
sd_db_ip = '127.0.0.1'
sd_db_user = 'root'
sd_db_pwd = ''

machine_name = 'Push_Data_DEV'

if_write_redis = False
index_dead_clock = '11:00'
flight_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/flight_index_md5'
train_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/train_index_md5'
hotel_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/hotel_index_md5'
bus_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/bus_index_md5'
car_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/car_index_md5'
rent_index_md5_file = '/search/redis_new/DataSearchIndex/index_file/rent_index_md5'

size_map = {}
size_map[flight_index_md5_file] = 100000000
size_map[hotel_index_md5_file] = 30000000
size_map[train_index_md5_file] = 50000000
size_map[bus_index_md5_file] = 200000
size_map[car_index_md5_file] = 250000
size_map[rent_index_md5_file] = 9000000
