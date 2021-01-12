import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthStore } from 'src/app/storemanagement/auth.store';

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
    private userService: AuthStore,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      username: new FormControl('', Validators.required),
      email: new FormControl('', [Validators.email]),
      password: new FormControl('', Validators.required),
    });
  }

  async register() {
    if (this.registerForm.valid) {
      try {
        await this.userService.register(
          this.registerForm.value.username,
          this.registerForm.value.password,
          this.registerForm.value.email
        );
        this.error = false;
      } catch (error) {
        this.error = true;
      }
    } else {
      this.error = true;
    }
  }

  login() {
    this.router.navigate(['/login']);
  }
}
