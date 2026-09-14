import std.math;
import std.typecons;
import std.array;
import std.algorithm;

string f(string s, string sep) 
{
    string[] parts = s.split(sep);
    string[] reverse = parts.map!(e => "*" ~ e).array;
    
    return reverse.reverse.join(";");
}
unittest
{
    alias candidate = f;

    assert(candidate("volume", "l") == "*ume;*vo");
}
void main(){}
