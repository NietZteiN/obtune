/*
  Write a function that takes an integer a and returns true
  if this ingeger is a cube of some integer number.
  Note: you may assume the input is always valid.
  Examples:
  iscube(1) ==> true
  iscube(2) ==> false
  iscube(-1) ==> true
  iscube(64) ==> true
  iscube(0) ==> true
  iscube(180) ==> false
  */
const iscube = (a) => {

  a = Math.abs(a);
  return (Math.pow(Math.round(Math.pow(a, 1.0 / 3.0)), 3) == a);
}

const testIscube = () => {
  console.assert(true === iscube(1))
  console.assert(false === iscube(2))
  console.assert(true === iscube(-1))
  console.assert(true === iscube(64))
  console.assert(false === iscube(180))
  console.assert(true === iscube(1000))
  console.assert(true === iscube(0))
  console.assert(false === iscube(1729))
}

testIscube()
