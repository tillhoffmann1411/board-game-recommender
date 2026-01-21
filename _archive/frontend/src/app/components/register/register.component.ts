import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthStore } from 'src/app/storemanagement/auth.store';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;

  error = false;

  constructor(
    private formBuilder: FormBuilder,
    private authStore: AuthStore,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      username: new FormControl('', Validators.required),
      email: new FormControl('', [Validators.email]),
      password: new FormControl('', Validators.required),
    });

    this.authStore.getError.subscribe(error => {
      if (error) {
        console.error(error);
        this.error = true;
      }
    });

    this.authStore.getIsLoggedIn.subscribe(isLoggedIn => {
      if (isLoggedIn) {
        this.router.navigate(['games']);
      }
    })
  }

  register() {
    if (this.registerForm.valid) {
      this.authStore.register(
        this.registerForm.value.username,
        this.registerForm.value.password,
        this.registerForm.value.email
      );
    } else {
      this.error = true;
    }
  }

  login() {
    this.router.navigate(['/login']);
  }
}
