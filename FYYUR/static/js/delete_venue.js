const button_delete = document.querySelectorAll('[id=delete-btn]')[0];
button_delete.onclick = function(e)
	{
		const venueItem = e.target.dataset['id'];
		fetch('/venues/' + venueItem + '/Delete', {
				method:'DELETE'
				,
				cache: "reload",
				headers: {
					'Content-Type' :'application/json'
				}}).then(function(){
			
			
			window.location.href ='/venues'
			
		}).catch(function() {
	        window.location.href ='/'
	    })
	}


	const button_delete_shows = document.querySelectorAll('[id=delete-show]');
	for(let i =0 ; i < button_delete_shows.length ; i++)
	{
		const button_delete_show = button_delete_shows[i]
		
		button_delete_show.onclick = function(e)
		{
			
			const venue = e.target.dataset['venue'];
			const showItem = e.target.dataset['id'];
			fetch('/shows/' + showItem + '/Delete', {
					method:'DELETE'
					,
					cache: "reload",
					headers: {
						'Content-Type' :'application/json'
					}}).then(function(){
				
				
				window.location.href ='/venues/' +venue
				
			}).catch(function() {
				window.location.href ='/'
			})
		}

	}
	
	