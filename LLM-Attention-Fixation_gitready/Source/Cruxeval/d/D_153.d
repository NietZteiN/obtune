import std.math;
import std.typecons;
import std.conv;

bool f(string text, string suffix, long num) 
{
    string str_num = to!string(num);
    return text.length >= suffix.length + str_num.length &&
           text[$-suffix.length-str_num.length .. $-suffix.length] == suffix &&
           text[$-str_num.length .. $] == str_num;
}
unittest
{
    alias candidate = f;

    assert(candidate("friends and love", "and", 3L) == false);
}
void main(){}
