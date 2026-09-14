import std.math;
import std.typecons;
import std.string;

string f(string text, long width) 
{
    string result = "";
    auto lines = text.split('\n');
    foreach (line; lines) {
        result ~= line.center(width);
        result ~= '\n';
    }

    // Remove the very last empty line
    if (!result.empty()) {
        result = result[0 .. $-1];
    }
    
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("l
l", 2L) == "l 
l ");
}
void main(){}
