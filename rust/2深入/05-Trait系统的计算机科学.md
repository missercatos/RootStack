# Trait

## 

### 

Rust trait 

****monomorphization `impl Trait for T` `call`

****dyn Trait vtable `&dyn Trait`  16B data_ptr + vtable_ptrvtable  trait  `call [vtable + offset]` 

****

- **VtableVirtual Table**
- **Fat Pointer** `&[T]`  ptr+len`&dyn Trait`  data_ptr+vtable_ptr
- **Monomorphization**
- **Object Safety**trait 

```text
 vs :

 ():
  fn process<T: Display>(item: &T) {
      println!("{}", item);
  }

  process(&42);       //  process_i32
  process(&"hello");  //  process_str

   (process_i32):
    call    i32::fmt          ; 
    ; :  fmt 
    ; 

 (trait object):
  fn process(item: &dyn Display) {
      println!("{}", item);
  }

  :
    mov     rax, [rdi + 8]    ; rax = vtable_ptr
    call    [rax + 16]        ;  vtable[2] (fmt )
    ; : 
    ; : ~10-15 CPU 

:
  : 1-3  ()
  : 10-15  ( + )
  
```

### Vtable 

```text
Vtable :

trait Animal {
    fn speak(&self);          //  1
    fn name(&self) -> &str;   //  2
    fn feed(&mut self, food: &str); //  3
}

struct Dog { name: String, age: u32 }
impl Animal for Dog {
    fn speak(&self) { println!("Woof!"); }
    fn name(&self) -> &str { &self.name }
    fn feed(&mut self, food: &str) { println!("Eating {}", food); }
}

Dog  vtable :

                Vtable for Dog               

 [0] drop_in_place fn ptr  ()        
 [1] size of Dog           (8 )          
 [2] align of Dog          (4 )          
 [3] speak fn ptr          → Dog::speak      
 [4] name fn ptr           → Dog::name       
 [5] feed fn ptr           → Dog::feed       


&dyn Animal :

 data_ptr  (8 bytes) → Dog      
 vtable_ptr (8 bytes) → vtable     

: 16 

vtable  trait 
```

###  (Orphan Rule)

trait coherence  `(Trait, Type)`  impl" crate " crate 

```text
:

: impl<T> Trait for T :
  1. Trait  crate 
  2. T  crate 

:
  crate A:
    trait MyTrait { ... }
    struct MyType { ... }

  crate B:
    impl MyTrait for MyType { ... }
    //  OK: MyTrait  crate A  MyType  crate A
    // ...

  :
    crate A  MyTrait
    crate B  MyType
    crate C:
      impl A::MyTrait for B::MyType { ... }
      //  : MyTrait  MyType  crate C 

    crate A:
      impl MyTrait for i32 { ... }
      //  OK: MyTrait  crate A 

    crate B:
      impl Display for MyType { ... }
      //  OK: MyType  crate B 

:
  :
    crate A: impl Display for Vec<i32> { fn fmt(...) { ... } }
    crate B: impl Display for Vec<i32> { fn fmt(...) { ... } }
    // ! Vec<i32>  Display 

:
  Newtype : struct Wrapper(Vec<i32>)
  : impl Display for Wrapper { ... }
  //  OK: Wrapper  crate 
```

### Object Safety 

```text
Object Safety :

 trait T  object-safe :

1. T :
   a.  Self ( receiver  Self )
   b. 
   c.  Self: Sized 

2. T 

3. T: Sized  T 

:

//  Object-safe
trait Display {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result;
    // self: &Self (OK)
    //  fmt::Result (OK,  Self)
}

//   object-safe:  Self
trait Clone {
    fn clone(&self) -> Self;
    //  Self →  vtable 
}

//   object-safe: 
trait Convertible<T> {
    fn convert(&self) -> T;
    //  T → vtable  T
}

//  Object-safe: Sized 
trait Foo {
    fn bar(&self);  //  Sized  → object-safe
    fn baz(&self) where Self: Sized { } //  Sized  → 
}

 Self :
  dyn Trait  vtable:
    [drop, size, align, method1, method2, ...]

   method  Self:
     Self 
    vtable 
     Self 
```

### Trait Upcasting ()

```rust
// Rust  trait upcasting 
//  &dyn SubTrait  &dyn SuperTrait

trait Animal {
    fn speak(&self);
}

trait Dog: Animal {
    fn fetch(&self);
}

let dog: &dyn Dog = &my_dog;
let animal: &dyn Animal = dog;  // trait upcasting

// vtable :
// Dog vtable: [drop, size, align, speak, fetch]
// Animal vtable: [drop, size, align, speak]
//
//  vtable 
```

###  (Coherence Rules)

```text
Coherence :

:  (Trait, Type) 

:

1.  (Orphan Rule):
   impl<T> Trait for T Trait  T  crate 

2.  (No Overlap):
    trait 
   impl Trait for T { ... }
   impl Trait for T { ... }  //  

3.  (Overlapping Coherence):
    Rust  (specialization)
    where 

:
  impl<T: Display> ToString for T { ... }  // blanket impl
  impl ToString for MyType { ... }         //   blanket impl 

Rust :
  -  blanket impl
  -  (specialization)  nightly 
  - min_specialization 
```

---

## 

### Vtable 

```rust
trait Animal { fn speak(&self); fn name(&self) -> &str; }
// vtable: [speak_ptr, name_ptr, drop_ptr, size, align]
```

### Object safety 

```rust
//  object-safe:  Self
trait Clone { fn clone(&self) -> Self; } // dyn Clone 

// Object-safe: Self 
trait Display { fn fmt(&self, f: &mut Formatter) -> fmt::Result; }
```

### Super-trait

```rust
trait Animal: Display {} // Animal  Display 
```

###  trait

```rust
trait Send {} // 
trait Sync {} // 
trait Copy {} // 
trait Sized {} // 
```

###  vs 

| | Static Dispatch | Dynamic Dispatch |
|--|----------------|------------------|
|  | 8B () | 16B () |
|  |  |  (vtable) |
|  |  () |  () |
|  |  |  |

### Vtable 

```rust
//  vtable 
use std::mem;

trait MyTrait {
    fn method(&self) -> i32;
}

struct A(i32);
impl MyTrait for A {
    fn method(&self) -> i32 { self.0 }
}

struct B(i32, i32);
impl MyTrait for B {
    fn method(&self) -> i32 { self.0 + self.1 }
}

let a: &dyn MyTrait = &A(10);
let b: &dyn MyTrait = &B(20, 30);

//  vtable 
// a.method() →  vtable_ptr A::method
// b.method() →  vtable_ptr B::method
println!("{}", a.method()); // 10
println!("{}", b.method()); // 50
```

---

## 

### Vtable 

```text
 vtable :

1.  trait 
   trait Animal {
       fn speak(&self);
       fn name(&self) -> &str;
   }
   : [speak, name]

2.  impl  vtable
   impl Animal for Dog { ... }
   vtable_Dog = [
       drop_in_place::<Dog>,   // [0] 
       size_of::<Dog>(),       // [1] 
       align_of::<Dog>(),      // [2] 
       Dog::speak as fn ptr,   // [3]  1
       Dog::name as fn ptr,    // [4]  2
   ]

3. 
   let dog: &dyn Animal = &my_dog;
   // data_ptr = &my_dog
   // vtable_ptr = &vtable_Dog

4. 
   animal.speak();
   // asm:
   //   mov rax, [rdi + 8]     ; rax = vtable_ptr
   //   call [rax + 24]        ;  vtable[3] (speak)
   //   ; 24 = 3 * 8 ( 3  8 )
```

### Trait 

```text
:

 ():
   
   
   
    Self 

 (trait object):
   
   
   
   

:
  : fn process<T: Display>(item: &T) { ... }
    -  process_i32, process_f64, ...
    - 
    - : 

  Trait object: fn process(item: &dyn Display) { ... }
    - 
    - 
    - : 

:
  // 
  fn sum<T: std::ops::Add<Output=T> + Copy>(a: T, b: T) -> T {
      a + b
  }
  sum(1, 2);        //  sum_i32
  sum(1.0, 2.0);    //  sum_f64

  // 
  trait Summable {
      fn add(&self, other: &Self) -> Self;
  }
  fn dynamic_sum(items: &[&dyn Summable]) { ... }
```

---

## 

### 

:  — sort_by trait

```rust
students.sort_by(|a, b| b.total.cmp(&a.total)
 .then_with(|| a.chinese.cmp(&b.chinese))
 .then_with(|| a.id.cmp(&b.id)));
// sort_by  trait bound 
// FnMut(&T, &T) -> Ordering
```
