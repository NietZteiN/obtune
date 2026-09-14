import std.array;
import std.string;

string[] f(string text, long chunks) 
{
    return text.split('\n').array();
}
unittest
{
    alias candidate = f;

    assert(candidate("/alcm@ an)t//eprw)/e!/d
ujv", 0L) == ["/alcm@ an)t//eprw)/e!/d", "ujv"]);
}
void main(){}
