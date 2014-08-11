<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="shortcut icon" href="../../assets/ico/favicon.ico">

    <title>KALAMAKOM</title>
     {{ HTML::style('css/bootstrap.min.css')}}
    {{ HTML::style('//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css')}}
    {{ HTML::style('css/sign_in.css')}}
    {{ HTML::style('css/style.css')}}
     {{ HTML::script('https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js'); }}
    {{ HTML::script('js/jquery-1.10.2.min.js') }}

  <body>
    
    <div class="container">
      @if(isset($message))
        {{$message}}
      @endif

      @if(!Auth::user())
      {{Form::open('users/adminstration/signin','',array('class'=>'form-signin'))}}
        <h2 class="form-signin-heading">Please sign in</h2>
        <input type="email" id="email" name="email" class="form-control" placeholder="Email address" required autofocus>
        <input type="password" id="password" name="password" class="form-control" placeholder="Password" required>
        <label class="checkbox">
          <input type="checkbox" name="remember-me" value="remember-me"> Remember me
        </label>
        <button class="btn btn-lg btn-primary btn-block" type="submit" id="submitBtn">Sign in</button>
      {{Form::close()}}
      @endif

      @if(Auth::user())
        

        <script type="text/javascript">
            // setTimeout(function(){
              setTimeout(function(){
                $('.fancybox-overlay ').click();
              },1000);
              // window.location.replace('www.google.com');
            // },2000);
        </script>
      @endif
    </div> 
     {{ HTML::script('js/bootstrap.min.js') }}
    {{ HTML::script('//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js') }}
    {{ HTML::script('js/effects.js') }}
   
    
  </body>
</html>