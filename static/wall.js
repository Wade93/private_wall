$(document).ready(function(){
    $('#username').keyup(function(){
        var data = $("#regForm").serialize()   // capture all the data in the form in the variable data
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: "/username",
            data: data
        })
        .done(function(res){
             $('#usernameMsg').html(res)  // manipulate the dom when the response comes back
        })
    })
    $('#searchbar').keyup(function(){
        console.log("IT'S WORKING")
        $.ajax({
            method: "GET",
            url: $(this).attr('action'),
            data: $(this).serialize()
        })
        .done(function(res){
             $('#search_results').html(res)  // manipulate the dom when the response comes back
        })
    })
    $('.trashcan').click(function(e){
        $('#received_msgs').html("")
        e.preventDefault()
        $.ajax({
            url: $(this).attr('href')
            console.log("LOGGING THE URL", url)
        })
        
        .done(function(){
             $(this.parents(".card mb-4")).remove()  // manipulate the dom when the response comes back
        })
        return false
    })
})