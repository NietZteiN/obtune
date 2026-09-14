import std.math;
import std.typecons;
import std.string;

string f(string text, string value) 
{
    auto result = text.split(value);
    return result[1] ~ result[0];
}
unittest
{
    alias candidate = f;

    assert(candidate("difkj rinpx", "k") == "j rinpxdif");
}
void main(){}
