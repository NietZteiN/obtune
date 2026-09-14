using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> strings) {
        List<string> new_strings = new List<string>();
        foreach (string str in strings)
        {
            string first_two = str.Length > 1 ? str.Substring(0,2) : str;
            if (first_two.StartsWith("a") || first_two.StartsWith("p"))
            {
                new_strings.Add(first_two);
            }
        }
        return new_strings;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"a", (string)"b", (string)"car", (string)"d"}))).SequenceEqual((new List<string>(new string[]{(string)"a"}))));
    }

}
