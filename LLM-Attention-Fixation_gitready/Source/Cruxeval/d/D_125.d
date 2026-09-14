import std.math;
import std.typecons;
import std.algorithm;
import std.conv;
import std.string;

string f(string text, long res) 
{
    foreach (c; "*\n\"") {
        text = text.replace(c, "!" ~ to!string(res));
    }
    
    if (text.startsWith("!")) {
        text = text[res.to!string.length .. $];
    }
    
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("\"Leap and the net will appear", 123L) == "3Leap and the net will appear");
}
void main(){}
