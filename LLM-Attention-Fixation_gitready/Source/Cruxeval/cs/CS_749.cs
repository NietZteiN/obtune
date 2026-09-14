using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long width) {
        string result = "";
        string[] lines = text.Split('\n');
        foreach(string l in lines)
        {
            result += l.PadLeft((int)width/2 + l.Length/2).PadRight((int)width);
            result += '\n';
        }
        // Remove the very last empty line
        result = result.Substring(0, result.Length - 1);
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("l\nl"), (2L)).Equals(("l \nl ")));
    }

}
