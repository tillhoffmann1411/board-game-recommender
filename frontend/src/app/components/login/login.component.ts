import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';
import { AuthStore } from '../../storemanagement/auth.store';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;

  error = false;

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthStore,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      username: new FormControl('', [Validators.required]),
      password: new FormControl('', Validators.required),
    });

    this.authService.getError.subscribe(error => {
      if (error) {
        console.error(error);
        this.error = true;
      }
    });

    this.authService.getIsLoggedIn.subscribe(isLoggedIn => {
      if (isLoggedIn) {
        this.router.navigate(['games']);
      }
    });
  }

  login() {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value.username, this.loginForm.value.password);
    } else {
      this.error = true;
    }
  }

  register() {
    this.router.navigate(['/register']);
  }

}
