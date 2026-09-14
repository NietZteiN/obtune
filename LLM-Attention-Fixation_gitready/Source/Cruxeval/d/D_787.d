import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    if (text.length == 0) {
        return "";
    }
    
    text = toLower(text);
    return text[0..1].toUpper() ~ text[1..$];
}
unittest
{
    alias candidate = f;

    assert(candidate("xzd") == "Xzd");
}
void main(){}
