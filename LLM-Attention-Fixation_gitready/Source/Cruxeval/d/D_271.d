import std.math;
import std.typecons;
import std.string;
import std.conv;
import std.algorithm;
import std.array;

string f(string text, string c) 
{
    if (!text.canFind(c)) {
        throw new Exception(format("Text has no %s", c));
    }
    auto index = text.lastIndexOf(c);
    string res = text[0..index] ~ text[(index+1)..$];
    return res;
}
unittest
{
    alias candidate = f;

    assert(candidate("uufhl", "l") == "uufh");
}
void main(){}
