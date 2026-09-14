import std.math;
import std.typecons;

bool isLowercase(char c) {
    return c >= 'a' && c <= 'z';
}

string f(string text) 
{
    for (size_t i = 0; i < text.length - 1; i++) {
        if (isLowercase(text[i])) {
            return text[i + 1..$];
        }
    }
    return "";
}
unittest
{
    alias candidate = f;

    assert(candidate("wrazugizoernmgzu") == "razugizoernmgzu");
}
void main(){}
