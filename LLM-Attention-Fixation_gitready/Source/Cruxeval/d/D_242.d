import std.math;
import std.typecons;
import std.array;
import std.string;

string[] rsplit(string str, string delimiter)
{
    size_t pos = str.lastIndexOf(delimiter);
    if (pos == -1)
    {
        return [str, ""];
    }
    return [str[0 .. pos], str[pos + delimiter.length .. $]];
}

string join(string[] arr, string delimiter)
{
    string result = "";
    foreach (i, elem; arr)
    {
        if (i != 0)
        {
            result ~= delimiter;
        }
        result ~= elem;
    }
    return result;
}

string f(string book)
{
    auto a = rsplit(book, ":");
    auto wordsBeforeColon = a[0].split(" ");
    auto wordsAfterColon = a[1].split(" ");
    
    if (wordsBeforeColon[$-1] == wordsAfterColon[0]) {
        return f(join(wordsBeforeColon[0 .. $-1], " ") ~ " " ~ a[1]);
    }
    
    return book;
}
unittest
{
    alias candidate = f;

    assert(candidate("udhv zcvi nhtnfyd :erwuyawa pun") == "udhv zcvi nhtnfyd :erwuyawa pun");
}
void main(){}
