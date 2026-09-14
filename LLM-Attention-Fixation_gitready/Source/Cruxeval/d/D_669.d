import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string t) 
{
    auto sep = "-";
    auto pos = t.lastIndexOf(sep);
    if (pos == -1) {
        return t;
    }
    
    auto a = t[0 .. pos];
    auto b = t[pos .. $];
    
    if (a.length == b.length) {
        return "imbalanced";
    }
    
    return a ~ b.replace(sep, "");
}
unittest
{
    alias candidate = f;

    assert(candidate("fubarbaz") == "fubarbaz");
}
void main(){}
