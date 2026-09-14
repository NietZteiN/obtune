import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, long tab_size) 
{
    return text.replace('\t', " ".replicate(tab_size));
}
unittest
{
    alias candidate = f;

    assert(candidate("a", 100L) == "a");
}
void main(){}
