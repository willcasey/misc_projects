select A.*, (max_price - min_price) as price_delta 
from 
(
	select category, product, discount, size, min(price) as min_price, max(price) as max_price, avg(price) as avg_price 
	from ah_inventory 
	group by 1, 2, 3, 4
) A 

where price_delta > 0
order by price_delta desc;
