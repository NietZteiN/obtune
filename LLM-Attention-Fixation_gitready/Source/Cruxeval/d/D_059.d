import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string f(string s) 
{
    auto a = s.strip().split("");
    auto b = a;
    foreach_reverse (c; a)
    {
        if (c == " ")
        {
            b.popBack();
        }
        else
        {
            break;
        }
    }
    return b.join();
}
unittest
{
    alias candidate = f;

    assert(candidate("hi ") == "hi");
}
void main(){}
