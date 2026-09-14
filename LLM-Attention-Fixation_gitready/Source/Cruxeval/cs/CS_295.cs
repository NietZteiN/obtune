using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> fruits) {
        if (fruits.Last() == fruits.First())
        {
            return new List<string>() { "no" };
        }
        else
        {
            fruits.RemoveAt(0);
            fruits.RemoveAt(fruits.Count - 1);
            fruits.RemoveAt(0);
            fruits.RemoveAt(fruits.Count - 1);
            return fruits;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"apple", (string)"apple", (string)"pear", (string)"banana", (string)"pear", (string)"orange", (string)"orange"}))).SequenceEqual((new List<string>(new string[]{(string)"pear", (string)"banana", (string)"pear"}))));
    }

}
