import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string letters) 
{
    string letters_only = letters.strip("., !?*");
    auto words = letters_only.split(" ");
    return words.join("....");
}
unittest
{
    alias candidate = f;

    assert(candidate("h,e,l,l,o,wo,r,ld,") == "h,e,l,l,o,wo,r,ld");
}
void main(){}
