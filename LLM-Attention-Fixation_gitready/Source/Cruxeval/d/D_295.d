import std.math;
import std.typecons;
string[] f(string[] fruits) 
{
    if (fruits[$ - 1] == fruits[0]) {
        return ["no"];
    } else {
        fruits = fruits[1..$-1];
        fruits = fruits[1..$-1];
        return fruits;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate(["apple", "apple", "pear", "banana", "pear", "orange", "orange"]) == ["pear", "banana", "pear"]);
}
void main(){}
