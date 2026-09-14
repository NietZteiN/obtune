import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string n, string m, string text) 
{
    if (text.strip().empty) {
        return text;
    }
    char head = text[0];
    string mid = text[1 .. $-1];
    char tail = text[$-1];
    string joined = to!string(head).replace(n, m) ~ mid.replace(n, m) ~ to!string(tail).replace(n, m);
    return joined;
}
unittest
{
    alias candidate = f;

    assert(candidate("x", "$", "2xz&5H3*1a@#a*1hris") == "2$z&5H3*1a@#a*1hris");
}
void main(){}
