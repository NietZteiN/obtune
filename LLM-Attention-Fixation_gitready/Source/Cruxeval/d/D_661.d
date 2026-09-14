import std.math;
import std.typecons;
import std.range;
import std.algorithm;

string f(string letters, long maxsplit) 
{
    auto split_words = letters.split();
    long num_words = split_words.length;
    long start_index = max(0, num_words - maxsplit);
    return split_words[start_index .. $].join("");
}
unittest
{
    alias candidate = f;

    assert(candidate("elrts,SS ee", 6L) == "elrts,SSee");
}
void main(){}
