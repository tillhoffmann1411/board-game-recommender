import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators, FormBuilder } from '@angular/forms';
import { UserHttpService } from 'src/app/services/user.service';
import { Router } from '@angular/router';

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
    private userService: UserHttpService,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      username: new FormControl('', Validators.required),
      firstName: new FormControl(''),
      lastName: new FormControl(''),
      email: new FormControl('', [Validators.email]),
      password: new FormControl('', Validators.required),
    });
  }

  async register() {
    if (this.registerForm.valid) {
      try {
        const response = await this.userService.register(
          this.registerForm.value.username,
          this.registerForm.value.password,
          this.registerForm.value.email
        );
        this.error = false;
        console.log('Register response:', response);
      } catch (error) {
        console.log('Could not register');
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
