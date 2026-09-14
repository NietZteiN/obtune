import std.math;
import std.typecons;
import std.string;

string f(string text, string chars) 
{
    if (chars.length > 0) {
        text = stripRight(text, chars);
    } else {
        text = stripRight(text, " ");
    }
    if (text == "") {
        return "-";
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("new-medium-performing-application - XQuery 2.2", "0123456789-") == "new-medium-performing-application - XQuery 2.");
}
void main(){}
