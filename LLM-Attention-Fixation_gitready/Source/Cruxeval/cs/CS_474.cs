using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string txt, long marker) {
        List<string> a = new List<string>();
        string[] lines = txt.Split('\n');
        foreach(string line in lines)
        {
            if (marker < 0)
            {
                a.Add(line);
            }
            else
            {
                int spaces = (int) (marker - line.Length) / 2;
                string centeredLine = line.PadLeft(line.Length + spaces).PadRight((int)marker);
                a.Add(centeredLine);
            }
        }
        return string.Join("\n", a);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("#[)[]>[^e>\n 8"), (-5L)).Equals(("#[)[]>[^e>\n 8")));
    }

}
