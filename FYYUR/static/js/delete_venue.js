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
	