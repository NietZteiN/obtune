import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string text, string speaker) 
{
    while (text.startsWith(speaker)) {
        text = text[speaker.length .. $];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("[CHARRUNNERS]Do you know who the other was? [NEGMENDS]", "[CHARRUNNERS]") == "Do you know who the other was? [NEGMENDS]");
}
void main(){}
