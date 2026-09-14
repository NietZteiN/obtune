import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string f(string text, string repl) 
{
    text = text.toLower();
    repl = repl.toLower();
    
    char[char] map;
    for(int i = 0; i < min(text.length, repl.length); i++) {
        map[text[i]] = repl[i];
    }
    
    foreach(char ch; text) {
        text = replace(text, ch, map.get(ch, ch));
    }

    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("upper case", "lower case") == "lwwer case");
}
void main(){}
