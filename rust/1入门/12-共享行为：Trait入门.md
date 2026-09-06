# Trait

## 

### Trait  Rust 

 + trait bound `&dyn Trait` / `Box<dyn Trait>`data pointer + vtable pointer16 vtable  trait 

```text
 (impl Trait / <T: Trait>):

 :                   
 fn speak_dog(dog: &Dog) { dog.speak(); }
 fn speak_cat(cat: &Cat) { cat.speak(); }
 :                   


 (dyn Trait):

 :  (16 )                 
                                           
 &dyn Speak = [data_ptr, vtable_ptr]       
                ↓          ↓               
            Dog         
                         drop: ...       
                         speak: ...      
                         introduce: …    
                            
 : (vtable.speak)(data_ptr)            

```

###  vs 

|  |  |  |
|------|----------|----------|
|  |  | vtable  |
|  |  |  |
|  |  |  |
|  |  | `Vec<Box<dyn Trait>>` |
|  |  |  |
|  |  |  trait |

### Orphan Rule

 trait  trait  crate  trait  crate 

```text
Orphan Rule :
- impl Trait for Type
- : Trait  crate  OR Type  crate 

:
 impl MyTrait for i32       (MyTrait )
 impl Display for MyStruct  (MyStruct )

:
 impl Display for Vec<i32>  ()
 impl Hash for i32          (Hash  i32 )
```

### derive 

`#[derive]`  trait 

```rust
#[derive(Debug, Clone, PartialEq)]
struct Point { x: f64, y: f64 }

//  ():
// impl Debug for Point {
//     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
//         f.debug_struct("Point")
//          .field("x", &self.x)
//          .field("y", &self.y)
//          .finish()
//     }
// }
// impl Clone for Point { ... } // 
// impl PartialEq for Point { ... } // 
```

### Display / Debug / Clone / Copy 

```text
Display vs Debug:
  Display:  ({})
    -  impl
    - 

  Debug:  ({:?})
    -  derive
    - 

Clone vs Copy:
  Clone:  (.clone())
    - 
    - 

  Copy:  ()
    - 
    -  Clone
    -  Copy
    -  Copy  clone() 

   Copy:
     i32, f64, bool, char
      Copy /
     String, Vec, Box ()
      ( Copy" Copy")
```

---

## 

### 

```rust
trait Speak {
    fn speak(&self); // 
    fn introduce(&self) -> String { // 
        format!("I can speak!")
    }
}

struct Dog;
impl Speak for Dog {
    fn speak(&self) { println!("Woof!"); }
    // introduce() 
}

struct Cat;
impl Speak for Cat {
    fn speak(&self) { println!("Meow!"); }
    fn introduce(&self) -> String {
        format!("I am a cat!")
    }
}
```

### Trait 

```rust
// impl Trait 
fn say(animal: &impl Speak) { animal.speak(); }

//  trait bound 
fn say<T: Speak>(animal: &T) { animal.speak(); }

// 
fn say_both<T: Speak>(a: &T, b: &T) {
    a.speak();
    b.speak();
}

// impl Trait 
fn say_both_impl(a: &impl Speak, b: &impl Speak) {
    a.speak();
    b.speak();
}
```

### Trait 

```rust
fn create() -> Box<dyn Speak> {
    Box::new(Dog)
}

// impl Trait 
fn create_dog() -> impl Speak {
    Dog
    // 
}
```

> `impl Trait`  `Box<dyn Trait>`

### derive 

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User { name: String, id: u32 }
```

| derive trait |  |  |
|-------------|----------|----------|
| `Debug` | `{:?}`  |  |
| `Clone` | `.clone()`  |  |
| `Copy` |  |  |
| `PartialEq` / `Eq` | `==` `!=`  |  |
| `PartialOrd` / `Ord` | `>` `<`  |  |
| `Hash` | HashMap  |  |
| `Default` | `Default::default()` |  |

### 

```rust
trait MyTrait { } //  crate  trait
impl MyTrait for i32 { } // trait 

// impl Display for Vec<i32> { } // trait 

// : Newtype 
struct MyVec(Vec<i32>);
impl std::fmt::Display for MyVec {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{:?}", self.0)
    }
}
// MyVec 
```

### 

```rust
fn dump<T: Display + Debug>(x: &T) {
    println!("Display: {}", x);
    println!("Debug: {:?}", x);
}

fn print_info(x: &(impl Area + Perimeter)) {
    println!(": {}, : {}", x.area(), x.perimeter());
}

// where 
fn complex_function<T, U>(t: &T, u: &U) -> String
where
    T: Display + Debug,
    U: Clone + Into<String>,
{
    format!("{}-{}", t, u.clone().into())
}
```

### trait 

```rust
// dyn Trait  sized 
let obj: Box<dyn Speak> = Box::new(Dog);  // Box 8  ()
let ref_obj: &dyn Speak = &Dog;           // & 16  (: data + vtable)

//  impl Trait  fat pointer
fn create() -> impl Speak { Dog }  // 
```

---

## 

###  1 impl Trait

```rust
//  
fn create(switch: bool) -> impl Speak {
    if switch { Dog } else { Cat }
    // : 
}

//   dyn Trait
fn create(switch: bool) -> Box<dyn Speak> {
    if switch { Box::new(Dog) } else { Box::new(Cat) }
}
```

###  2Copy  Clone 

```rust
// Copy 
let x: i32 = 5;
let y = x;  // x 
println!("{} {}", x, y);  // 

// Clone 
let s1 = String::from("hello");
let s2 = s1.clone();  // 
// println!("{}", s1);  //  s1 

//   s1
let s3 = s1;
// println!("{}", s1);  // : s1 
```

### 

1.  `impl Trait` 
2.  `Box<dyn Trait>`
3.  trait 
4. `derive`  `Copy`  Copy

---

## 

### 

:  — trait + derive

```rust
#[derive(Debug, Clone, PartialEq)]
struct Student { id: u32, grade: u32 }

impl Eq for Student {}

impl PartialOrd for Student {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        self.grade.partial_cmp(&other.grade)
    }
}

impl Ord for Student {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.grade.cmp(&other.grade)
    }
}
```

:  — trait 

```rust
trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> &str;
}

struct Circle { radius: f64 }
impl Shape for Circle {
    fn area(&self) -> f64 { std::f64::consts::PI * self.radius.powi(2) }
    fn name(&self) -> &str { "Circle" }
}

struct Rectangle { width: f64, height: f64 }
impl Shape for Rectangle {
    fn area(&self) -> f64 { self.width * self.height }
    fn name(&self) -> &str { "Rectangle" }
}

fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}
```
