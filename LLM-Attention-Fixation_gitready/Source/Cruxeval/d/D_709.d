import std.math;
import std.typecons;
import std.array;
import std.algorithm;

string f(string text) 
{
    auto my_list = text.split();
    my_list.sort!("a > b");
    return my_list.join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate("a loved") == "loved a");
}
void main(){}
