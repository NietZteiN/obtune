using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<string> bots) {
        List<string> clean = new List<string>();
        foreach (string username in bots)
        {
            if (!username.Equals(username.ToUpper()))
            {
                clean.Add(username.Substring(0, 2) + username.Substring(username.Length - 3));
            }
        }
        return clean.Count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"yR?TAJhIW?n", (string)"o11BgEFDfoe", (string)"KnHdn2vdEd", (string)"wvwruuqfhXbGis"}))) == (4L));
    }

}
