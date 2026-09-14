import std.math;
import std.typecons;
string f(string text, string suffix) 
{
    string output = text;
    while (text[$-suffix.length .. $] == suffix) {
        output = text[0 .. $-suffix.length];
        text = output;
    }
    return output;
}
unittest
{
    alias candidate = f;

    assert(candidate("!klcd!ma:ri", "!") == "!klcd!ma:ri");
}
void main(){}
