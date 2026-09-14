import std.math;
import std.typecons;
import std.string;

string f(string text, long tabsize) 
{
    string tab = " ";
    tab.length = tabsize;
    return text.replace("\t", tab);
}
unittest
{
    alias candidate = f;

    assert(candidate("	f9
	ldf9
	adf9!
	f9?", 1L) == " f9
 ldf9
 adf9!
 f9?");
}
void main(){}
