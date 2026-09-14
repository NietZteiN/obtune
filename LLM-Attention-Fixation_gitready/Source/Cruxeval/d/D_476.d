import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

bool f(string a, string split_on) 
{
    auto t = a.split();
    char[] aa = cast(char[])a;
    return count(aa, split_on) > 0;
}
unittest
{
    alias candidate = f;

    assert(candidate("booty boot-boot bootclass", "k") == false);
}
void main(){}
