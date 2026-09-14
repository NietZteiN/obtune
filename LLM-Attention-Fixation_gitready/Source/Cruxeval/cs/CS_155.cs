using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string ip, long n) {
        int i = 0;
        string outStr = "";
        foreach(char c in ip)
        {
            if (i == n)
            {
                outStr += '\n';
                i = 0;
            }
            i++;
            outStr += c;
        }
        return outStr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dskjs hjcdjnxhjicnn"), (4L)).Equals(("dskj\ns hj\ncdjn\nxhji\ncnn")));
    }

}
