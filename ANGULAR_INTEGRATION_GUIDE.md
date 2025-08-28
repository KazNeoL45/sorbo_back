# Angular Integration Guide for Success Page Communication

This guide explains how to handle the success page communication in your Angular application when users complete their orders through Stripe.

## Table of Contents

1. [Overview](#overview)
2. [Setup Instructions](#setup-instructions)
3. [Service Implementation](#service-implementation)
4. [Component Integration](#component-integration)
5. [Environment Configuration](#environment-configuration)
6. [Testing](#testing)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)
9. [Customizing Success Page Colors](#customizing-success-page-colors)

## Overview

When a user completes a payment through Stripe, they are redirected to a success page hosted by your Django backend. The backend now returns JSON data instead of HTML, which your Angular frontend can handle to display the appropriate success/cancel page and manage navigation.

The communication flow:
1. User completes payment → Stripe redirects to success page
2. Backend returns JSON with order details and redirect URL
3. Angular app handles the response and shows appropriate page
4. User sees success/cancel page within your Angular app

## Setup Instructions

### 1. Create the Order Success Service

Create a new service file: `src/app/services/order-success.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface OrderSuccessResponse {
  success: boolean;
  message: string;
  order: {
    id: string;
    status: string;
    created_at: string;
    updated_at: string;
    product: {
      name: string;
      price_pesos: string;
      currency: string;
      current_stock: number;
    };
    client_name: string;
    client_email: string;
  };
  redirect_url: string;
}

@Injectable({
  providedIn: 'root'
})
export class OrderSuccessService {
  private orderSuccessSubject = new BehaviorSubject<OrderSuccessResponse | null>(null);
  public orderSuccess$ = this.orderSuccessSubject.asObservable();

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  /**
   * Handle order success/cancel from URL parameters
   * This should be called when the app loads with order_id in URL
   */
  public handleOrderResult(orderId: string, endpoint: 'success' | 'cancel' = 'success'): Observable<OrderSuccessResponse> {
    const url = `${environment.backendUrl}/api/orders/${orderId}/${endpoint}/`;
    return this.http.get<OrderSuccessResponse>(url);
  }

  /**
   * Process order result and navigate accordingly
   */
  public processOrderResult(response: OrderSuccessResponse): void {
    this.orderSuccessSubject.next(response);
    
    // Navigate to the appropriate page
    if (response.success) {
      this.router.navigate(['/success'], { 
        state: { orderData: response.order } 
      });
    } else {
      this.router.navigate(['/cancel'], { 
        state: { orderData: response.order } 
      });
    }
  }

  /**
   * Get current order result
   */
  public getCurrentOrderResult(): OrderSuccessResponse | null {
    return this.orderSuccessSubject.value;
  }
}
```

### 2. Create Success and Cancel Components

**Success Component: `src/app/components/order-success/order-success.component.ts`**

```typescript
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OrderSuccessService } from '../../services/order-success.service';

@Component({
  selector: 'app-order-success',
  template: `
    <div class="success-container">
      <div class="success-icon">✓</div>
      <h1>¡Orden Completada!</h1>
      <p class="message">Tu pago ha sido procesado exitosamente. Gracias por tu compra.</p>
      
      <div class="order-details" *ngIf="orderData">
        <div class="detail-row">
          <span class="label">ID de Orden:</span>
          <span class="value">{{ orderData.id }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Producto:</span>
          <span class="value">{{ orderData.product.name }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Precio:</span>
          <span class="value">${{ orderData.product.price_pesos }} {{ orderData.product.currency }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Estado:</span>
          <span class="value status">{{ orderData.status.toUpperCase() }}</span>
        </div>
      </div>
      
      <button (click)="goHome()" class="home-button">Volver al Inicio</button>
    </div>
  `,
  styleUrls: ['./order-success.component.scss']
})
export class OrderSuccessComponent implements OnInit {
  orderData: any;

  constructor(
    private router: Router,
    private orderSuccessService: OrderSuccessService
  ) {
    // Get order data from router state
    const navigation = this.router.getCurrentNavigation();
    this.orderData = navigation?.extras?.state?.['orderData'];
  }

  ngOnInit(): void {
    // If no order data in state, try to get from service
    if (!this.orderData) {
      this.orderData = this.orderSuccessService.getCurrentOrderResult()?.order;
    }
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}
```

**Cancel Component: `src/app/components/order-cancel/order-cancel.component.ts`**

```typescript
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OrderSuccessService } from '../../services/order-success.service';

@Component({
  selector: 'app-order-cancel',
  template: `
    <div class="cancel-container">
      <div class="cancel-icon">✕</div>
      <h1>Orden Cancelada</h1>
      <p class="message">Tu orden ha sido cancelada. No se ha procesado ningún pago.</p>
      
      <div class="order-details" *ngIf="orderData">
        <div class="detail-row">
          <span class="label">ID de Orden:</span>
          <span class="value">{{ orderData.id }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Producto:</span>
          <span class="value">{{ orderData.product.name }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Estado:</span>
          <span class="value status">{{ orderData.status.toUpperCase() }}</span>
        </div>
      </div>
      
      <div class="button-group">
        <button (click)="goHome()" class="home-button">Volver al Inicio</button>
        <button (click)="viewProducts()" class="retry-button">Ver Productos</button>
      </div>
    </div>
  `,
  styleUrls: ['./order-cancel.component.scss']
})
export class OrderCancelComponent implements OnInit {
  orderData: any;

  constructor(
    private router: Router,
    private orderSuccessService: OrderSuccessService
  ) {
    // Get order data from router state
    const navigation = this.router.getCurrentNavigation();
    this.orderData = navigation?.extras?.state?.['orderData'];
  }

  ngOnInit(): void {
    // If no order data in state, try to get from service
    if (!this.orderData) {
      this.orderData = this.orderSuccessService.getCurrentOrderResult()?.order;
    }
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  viewProducts(): void {
    this.router.navigate(['/products']);
  }
}
```

### 3. Update App Component to Handle URL Parameters

Update your main app component: `src/app/app.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { OrderSuccessService } from './services/order-success.service';

@Component({
  selector: 'app-root',
  template: `
    <div>
      <!-- Your app content -->
      <router-outlet></router-outlet>
    </div>
  `
})
export class AppComponent implements OnInit {
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private orderSuccessService: OrderSuccessService
  ) {}

  ngOnInit(): void {
    // Check if we have order_id and status in URL parameters
    this.route.queryParams.subscribe(params => {
      const orderId = params['order_id'];
      const status = params['status'];
      
      if (orderId) {
        this.handleOrderResult(orderId, status);
      }
    });
  }

  private handleOrderResult(orderId: string, status?: string): void {
    // Determine which endpoint to call based on status
    const endpoint = status === 'cancel' ? 'cancel' : 'success';
    
    this.orderSuccessService.handleOrderResult(orderId, endpoint).subscribe({
      next: (response) => {
        this.orderSuccessService.processOrderResult(response);
      },
      error: (error) => {
        console.error('Error handling order result:', error);
        // Redirect to home on error
        this.router.navigate(['/']);
      }
    });
  }
}
```

### 4. Environment Configuration

**`src/environments/environment.ts` (Development)**
```typescript
export const environment = {
  production: false,
  backendUrl: 'http://localhost:8000'
};
```

**`src/environments/environment.prod.ts` (Production)**
```typescript
export const environment = {
  production: true,
  backendUrl: 'https://your-production-domain.com'
};
```

### 5. App Module Configuration

Update your `src/app/app.module.ts`:

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule, Routes } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { OrderSuccessComponent } from './components/order-success/order-success.component';
import { OrderCancelComponent } from './components/order-cancel/order-cancel.component';
import { OrderSuccessService } from './services/order-success.service';

const routes: Routes = [
  { path: 'success', component: OrderSuccessComponent },
  { path: 'cancel', component: OrderCancelComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  // Add your other routes here
];

@NgModule({
  declarations: [
    AppComponent,
    OrderSuccessComponent,
    OrderCancelComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes)
  ],
  providers: [
    OrderSuccessService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

## Service Implementation

### Basic Service

The service handles API calls and navigation:

```typescript
@Injectable({
  providedIn: 'root'
})
export class OrderSuccessService {
  private orderSuccessSubject = new BehaviorSubject<OrderSuccessResponse | null>(null);
  public orderSuccess$ = this.orderSuccessSubject.asObservable();

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  public handleOrderResult(orderId: string): Observable<OrderSuccessResponse> {
    const url = `${environment.backendUrl}/api/orders/${orderId}/success/`;
    return this.http.get<OrderSuccessResponse>(url);
  }

  public processOrderResult(response: OrderSuccessResponse): void {
    this.orderSuccessSubject.next(response);
    
    if (response.success) {
      this.router.navigate(['/success'], { 
        state: { orderData: response.order } 
      });
    } else {
      this.router.navigate(['/cancel'], { 
        state: { orderData: response.order } 
      });
    }
  }
}
```

## Component Integration

### App Component Integration

The app component checks for order_id in URL parameters and handles the result:

```typescript
export class AppComponent implements OnInit {
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private orderSuccessService: OrderSuccessService
  ) {}

  ngOnInit(): void {
    // Check if we have order_id in URL parameters
    this.route.queryParams.subscribe(params => {
      const orderId = params['order_id'];
      if (orderId) {
        this.handleOrderResult(orderId);
      }
    });
  }

  private handleOrderResult(orderId: string): void {
    this.orderSuccessService.handleOrderResult(orderId).subscribe({
      next: (response) => {
        this.orderSuccessService.processOrderResult(response);
      },
      error: (error) => {
        console.error('Error handling order result:', error);
        this.router.navigate(['/']);
      }
    });
  }
}
```

## Environment Configuration

### Development Environment

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  backendUrl: 'http://localhost:8000'
};
```

### Production Environment

```typescript
// src/environments/environment.prod.ts
export const environment = {
  production: true,
  backendUrl: 'https://your-production-domain.com'
};
```

## Testing

### Manual Testing

You can test the integration by visiting the success/cancel URLs directly:

```
# Success page
http://localhost:4200?order_id=YOUR_ORDER_ID&status=success

# Cancel page  
http://localhost:4200?order_id=YOUR_ORDER_ID&status=cancel
```

### Unit Testing

Create tests for your service: `src/app/services/order-success.service.spec.ts`

```typescript
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { OrderSuccessService } from './order-success.service';

describe('OrderSuccessService', () => {
  let service: OrderSuccessService;
  let httpMock: HttpTestingController;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        OrderSuccessService,
        { provide: Router, useValue: routerSpy }
      ]
    });
    
    service = TestBed.inject(OrderSuccessService);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should handle order success', () => {
    const mockResponse = {
      success: true,
      message: 'Order completed successfully',
      order: {
        id: '123',
        status: 'success',
        product: {
          name: 'Test Product',
          price_pesos: '100',
          currency: 'USD'
        }
      },
      redirect_url: '/success'
    };

    service.handleOrderResult('123', 'success').subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/orders/123/success/');
    expect(req.request.method).toBe('GET');
    req.flush(mockResponse);
  });

  it('should handle order cancel', () => {
    const mockResponse = {
      success: false,
      message: 'Order was cancelled',
      order: {
        id: '123',
        status: 'failed',
        product: {
          name: 'Test Product',
          price_pesos: '100',
          currency: 'USD'
        }
      },
      redirect_url: '/cancel'
    };

    service.handleOrderResult('123', 'cancel').subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/orders/123/cancel/');
    expect(req.request.method).toBe('GET');
    req.flush(mockResponse);
  });
});
```

## Security Considerations

### 1. URL Parameter Validation

Validate the order_id parameter:

```typescript
private handleOrderResult(orderId: string): void {
  // Validate order_id format
  if (!orderId || !/^\d+$/.test(orderId)) {
    console.error('Invalid order ID format');
    this.router.navigate(['/']);
    return;
  }

  this.orderSuccessService.handleOrderResult(orderId).subscribe({
    next: (response) => {
      this.orderSuccessService.processOrderResult(response);
    },
    error: (error) => {
      console.error('Error handling order result:', error);
      this.router.navigate(['/']);
    }
  });
}
```

### 2. Error Handling

Implement proper error handling:

```typescript
public handleOrderResult(orderId: string): Observable<OrderSuccessResponse> {
  const url = `${environment.backendUrl}/api/orders/${orderId}/success/`;
  return this.http.get<OrderSuccessResponse>(url).pipe(
    catchError((error) => {
      console.error('Error fetching order result:', error);
      throw error;
    })
  );
}
```

## Troubleshooting

### Common Issues

1. **Order not found**
   - Check if the order_id is correct
   - Verify the order exists in the database
   - Check backend logs for errors

2. **Navigation not working**
   - Ensure routes are properly configured
   - Check if components are declared in the module
   - Verify router state is being passed correctly

3. **API errors**
   - Check CORS configuration
   - Verify backend URL is correct
   - Check network connectivity

### Debug Mode

Add debug logging to help troubleshoot:

```typescript
private handleOrderResult(orderId: string): void {
  console.log('Handling order result for ID:', orderId);
  
  this.orderSuccessService.handleOrderResult(orderId).subscribe({
    next: (response) => {
      console.log('Order result received:', response);
      this.orderSuccessService.processOrderResult(response);
    },
    error: (error) => {
      console.error('Error handling order result:', error);
      this.router.navigate(['/']);
    }
  });
}
```

### Testing Checklist

- [ ] Service is created and injected properly
- [ ] HTTP client is imported and configured
- [ ] Environment configuration is correct
- [ ] Routes are properly configured
- [ ] Components are declared in the module
- [ ] Error handling is in place
- [ ] Unit tests are passing

## Additional Resources

- [Angular Router Documentation](https://angular.io/guide/router)
- [Angular Services Documentation](https://angular.io/guide/services)
- [Angular HTTP Client](https://angular.io/guide/http)
- [Angular Environment Configuration](https://angular.io/guide/build#configuring-application-environments)
- [Angular Testing Guide](https://angular.io/guide/testing)

## Support

If you encounter issues:

1. Check the browser console for errors
2. Verify your environment configuration
3. Test the API endpoints directly
4. Check the network tab for HTTP errors
5. Review the Angular documentation for updates

---

**Note**: This guide assumes you're using Angular 12+ and follows Angular best practices. Adjust the code according to your specific Angular version and project requirements.

## Customizing Success Page Colors

You can easily customize the success page colors by modifying the CSS styles. Here are several color schemes you can use:

### 1. Create the Success Component Stylesheet

Create the file: `src/app/components/order-success/order-success.component.scss`

#### Option A: Green Success Theme (Default)
```scss
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .success-icon {
    width: 80px;
    height: 80px;
    background: #4CAF50;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
    animation: bounce 0.6s ease-in-out;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .message {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    max-width: 500px;
    line-height: 1.6;
  }

  .order-details {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    max-width: 500px;
    width: 100%;

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-weight: 500;
        opacity: 0.8;
      }

      .value {
        font-weight: 600;
        
        &.status {
          color: #4CAF50;
          font-weight: 700;
        }
      }
    }
  }

  .home-button {
    background: linear-gradient(45deg, #4CAF50, #45a049);
    color: white;
    border: none;
    padding: 15px 40px;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    text-decoration: none;
    display: inline-block;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
      background: linear-gradient(45deg, #45a049, #4CAF50);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
```

#### Option B: Blue Professional Theme
```scss
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .success-icon {
    width: 80px;
    height: 80px;
    background: #2196F3;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(33, 150, 243, 0.3);
    animation: pulse 2s infinite;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .message {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    max-width: 500px;
    line-height: 1.6;
  }

  .order-details {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    max-width: 500px;
    width: 100%;

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-weight: 500;
        opacity: 0.8;
      }

      .value {
        font-weight: 600;
        
        &.status {
          color: #2196F3;
          font-weight: 700;
        }
      }
    }
  }

  .home-button {
    background: linear-gradient(45deg, #2196F3, #1976D2);
    color: white;
    border: none;
    padding: 15px 40px;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    text-decoration: none;
    display: inline-block;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
      background: linear-gradient(45deg, #1976D2, #2196F3);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(33, 150, 243, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0);
  }
}
```

#### Option C: Purple Modern Theme
```scss
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .success-icon {
    width: 80px;
    height: 80px;
    background: #9C27B0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(156, 39, 176, 0.3);
    animation: rotate 0.8s ease-in-out;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .message {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    max-width: 500px;
    line-height: 1.6;
  }

  .order-details {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    max-width: 500px;
    width: 100%;

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-weight: 500;
        opacity: 0.8;
      }

      .value {
        font-weight: 600;
        
        &.status {
          color: #9C27B0;
          font-weight: 700;
        }
      }
    }
  }

  .home-button {
    background: linear-gradient(45deg, #9C27B0, #7B1FA2);
    color: white;
    border: none;
    padding: 15px 40px;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
    text-decoration: none;
    display: inline-block;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(156, 39, 176, 0.4);
      background: linear-gradient(45deg, #7B1FA2, #9C27B0);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg) scale(0.8);
  }
  to {
    transform: rotate(360deg) scale(1);
  }
}
```

#### Option D: Orange Warm Theme
```scss
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .success-icon {
    width: 80px;
    height: 80px;
    background: #FF9800;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(255, 152, 0, 0.3);
    animation: slideIn 0.6s ease-out;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .message {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    max-width: 500px;
    line-height: 1.6;
  }

  .order-details {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    max-width: 500px;
    width: 100%;

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-weight: 500;
        opacity: 0.8;
      }

      .value {
        font-weight: 600;
        
        &.status {
          color: #FF9800;
          font-weight: 700;
        }
      }
    }
  }

  .home-button {
    background: linear-gradient(45deg, #FF9800, #F57C00);
    color: white;
    border: none;
    padding: 15px 40px;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
    text-decoration: none;
    display: inline-block;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
      background: linear-gradient(45deg, #F57C00, #FF9800);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### 2. Custom Color Variables

You can also create a more flexible system using CSS variables. Add this to your global styles or component:

```scss
:root {
  --success-primary: #4CAF50;
  --success-secondary: #45a049;
  --success-accent: #2196F3;
  --success-warm: #FF9800;
  --success-purple: #9C27B0;
  
  --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --card-background: rgba(255, 255, 255, 0.1);
  --text-primary: white;
  --text-secondary: rgba(255, 255, 255, 0.8);
}
```

### 3. Dark Theme Option

```scss
.success-container.dark-theme {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  
  .success-icon {
    background: #00C851;
    box-shadow: 0 4px 20px rgba(0, 200, 81, 0.3);
  }
  
  .order-details {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .home-button {
    background: linear-gradient(45deg, #00C851, #007E33);
    
    &:hover {
      background: linear-gradient(45deg, #007E33, #00C851);
    }
  }
}
```

### 4. How to Apply Different Themes

You can apply different themes by adding CSS classes to your component:

```typescript
// In your component
export class OrderSuccessComponent implements OnInit {
  theme: string = 'green'; // or 'blue', 'purple', 'orange', 'dark'
  
  get themeClass(): string {
    return `theme-${this.theme}`;
  }
}
```

```html
<!-- In your template -->
<div class="success-container" [ngClass]="themeClass">
  <!-- Your content -->
</div>
```

### 5. Responsive Design

Add these media queries for better mobile experience:

```scss
@media (max-width: 768px) {
  .success-container {
    padding: 1rem;
    
    h1 {
      font-size: 2rem;
    }
    
    .message {
      font-size: 1rem;
    }
    
    .order-details {
      padding: 1.5rem;
      
      .detail-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }
    }
    
    .home-button {
      padding: 12px 30px;
      font-size: 1rem;
    }
  }
}
```

### 6. Animation Options

You can choose different animations for the success icon:

- **Bounce**: `@keyframes bounce` (Option A)
- **Pulse**: `@keyframes pulse` (Option B)  
- **Rotate**: `@keyframes rotate` (Option C)
- **Slide In**: `@keyframes slideIn` (Option D)

### 7. Quick Color Switcher

To easily switch between themes, you can create a simple service:

```typescript
// src/app/services/theme.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type ThemeType = 'green' | 'blue' | 'purple' | 'orange' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private currentTheme = new BehaviorSubject<ThemeType>('green');
  public currentTheme$ = this.currentTheme.asObservable();

  setTheme(theme: ThemeType): void {
    this.currentTheme.next(theme);
  }

  getCurrentTheme(): ThemeType {
    return this.currentTheme.value;
  }
}
```

Choose the color scheme that best matches your brand or create your own custom colors by modifying the hex values in the CSS!
