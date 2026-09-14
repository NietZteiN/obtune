import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, string delim) 
{
    auto parts = text.split(delim);
    return parts[1] ~ delim ~ parts[0];
}
unittest
{
    alias candidate = f;

    assert(candidate("bpxa24fc5.", ".") == ".bpxa24fc5");
}
void main(){}
