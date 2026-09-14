using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string a) {
        a = a.Replace('/', ':');
        int colonIndex = a.LastIndexOf(':');
        if(colonIndex == -1)
        {
            return new List<string>{a, "", ""};
        }

        string first = a.Substring(0, colonIndex);
        string colon = a[colonIndex].ToString();
        string last = a.Substring(colonIndex + 1);

        return new List<string>{first, colon, last};
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("/CL44     ")).SequenceEqual((new List<string>(new string[]{(string)"", (string)":", (string)"CL44     "}))));
    }

}
