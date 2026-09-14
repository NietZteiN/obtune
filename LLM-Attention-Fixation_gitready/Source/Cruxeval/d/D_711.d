import std.math;
import std.typecons;
import std.array;

string f(string text) 
{
    return text.replace('\n', '\t');
}
unittest
{
    alias candidate = f;

    assert(candidate("apples
	
pears
	
bananas") == "apples			pears			bananas");
}
void main(){}
