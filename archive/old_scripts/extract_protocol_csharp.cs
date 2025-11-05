using System;
using System.Reflection;
using System.Linq;
using System.IO;
using System.Text;
using System.Collections.Generic;

class ProtocolExtractor
{
    static void Main(string[] args)
    {
        try
        {
            string exePath = "TK11.exe";
            if (!File.Exists(exePath))
            {
                Console.WriteLine("ERROR: " + exePath + " not found!");
                return;
            }

            Console.WriteLine("="  * 80);
            Console.WriteLine("TK11 BOOTLOADER PROTOCOL EXTRACTION");
            Console.WriteLine("=" + new string('=', 79));
            Console.WriteLine();

            // Load assembly
            Assembly assembly = Assembly.LoadFrom(exePath);
            Console.WriteLine("[+] Assembly loaded\n");

            // Find protocol_struct class
            Type protocolStruct = null;
            foreach (Type t in assembly.GetTypes())
            {
                if (t.FullName != null && t.FullName.Contains("protocol_struct"))
                {
                    protocolStruct = t;
                    break;
                }
            }

            if (protocolStruct == null)
            {
                Console.WriteLine("[-] protocol_struct class not found");
                return;
            }

            Console.WriteLine("[+] Found class: " + protocolStruct.FullName);
            Console.WriteLine();

            StringBuilder report = new StringBuilder();
            report.AppendLine("=" + new string('=', 79));
            report.AppendLine("TK11 BOOTLOADER PROTOCOL DOCUMENTATION");
            report.AppendLine("=" + new string('=', 79));
            report.AppendLine();

            // Extract all fields
            FieldInfo[] fields = protocolStruct.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);

            report.AppendLine("FIELDS AND CONSTANTS");
            report.AppendLine(new string('-', 80));
            report.AppendLine();

            foreach (FieldInfo field in fields)
            {
                report.AppendLine("Field: " + field.Name);
                report.AppendLine("  Type: " + field.FieldType.Name);
                report.AppendLine("  Static: " + field.IsStatic + ", Literal: " + field.IsLiteral);

                // Try to get constant value
                if (field.IsStatic && field.IsLiteral)
                {
                    try
                    {
                        object val = field.GetRawConstantValue();
                        if (val is int || val is uint || val is byte || val is short || val is ushort || val is long || val is ulong)
                        {
                            report.AppendLine(string.Format("  VALUE: {0} (0x{0:X})", val));
                        }
                        else
                        {
                            report.AppendLine("  VALUE: " + val);
                        }
                    }
                    catch { }
                }
                else if (field.IsStatic && field.IsPublic)
                {
                    try
                    {
                        object val = field.GetValue(null);
                        if (val != null)
                        {
                            report.AppendLine("  VALUE: " + val);
                        }
                    }
                    catch { }
                }

                report.AppendLine();
            }

            // Extract methods
            MethodInfo[] methods = protocolStruct.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);

            report.AppendLine();
            report.AppendLine("METHODS");
            report.AppendLine(new string('-', 80));
            report.AppendLine();

            foreach (MethodInfo method in methods)
            {
                // Skip property accessors and special methods
                if (method.Name.StartsWith("get_") || method.Name.StartsWith("set_") ||
                    method.Name.StartsWith(".") || method.Name.StartsWith("add_") || method.Name.StartsWith("remove_"))
                    continue;

                report.AppendLine("Method: " + method.Name);
                report.AppendLine("  Returns: " + method.ReturnType.Name);

                ParameterInfo[] parameters = method.GetParameters();
                if (parameters.Length > 0)
                {
                    report.AppendLine("  Parameters:");
                    foreach (ParameterInfo param in parameters)
                    {
                        report.AppendLine("    - " + param.ParameterType.Name + " " + param.Name);
                    }
                }

                report.AppendLine();
            }

            // Extract nested types (message structures)
            Type[] nestedTypes = protocolStruct.GetNestedTypes(BindingFlags.Public | BindingFlags.NonPublic);

            if (nestedTypes.Length > 0)
            {
                report.AppendLine();
                report.AppendLine("NESTED MESSAGE STRUCTURES");
                report.AppendLine(new string('-', 80));
                report.AppendLine();

                foreach (Type nested in nestedTypes)
                {
                    report.AppendLine("Structure: " + nested.Name);

                    FieldInfo[] structFields = nested.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);

                    int totalSize = 0;
                    int offset = 0;

                    foreach (FieldInfo sf in structFields)
                    {
                        int size = 0;
                        string sizeStr = "";

                        if (sf.FieldType == typeof(byte))
                        {
                            size = 1;
                            sizeStr = "[1 byte]";
                        }
                        else if (sf.FieldType == typeof(UInt16) || sf.FieldType == typeof(Int16))
                        {
                            size = 2;
                            sizeStr = "[2 bytes]";
                        }
                        else if (sf.FieldType == typeof(UInt32) || sf.FieldType == typeof(Int32))
                        {
                            size = 4;
                            sizeStr = "[4 bytes]";
                        }
                        else if (sf.FieldType == typeof(byte[]))
                        {
                            // Try to get array size from MarshalAs attribute
                            object[] attrs = sf.GetCustomAttributes(typeof(System.Runtime.InteropServices.MarshalAsAttribute), false);
                            if (attrs.Length > 0)
                            {
                                var marshalAttr = (System.Runtime.InteropServices.MarshalAsAttribute)attrs[0];
                                size = marshalAttr.SizeConst;
                                sizeStr = string.Format("[{0} bytes array]", size);
                            }
                            else
                            {
                                sizeStr = "[byte array - size unknown]";
                            }
                        }
                        else
                        {
                            sizeStr = "[" + sf.FieldType.Name + "]";
                        }

                        report.AppendLine(string.Format("  Offset 0x{0:X4} ({0,4}): {1,-30} {2,-20} {3}",
                            offset, sf.Name, sf.FieldType.Name, sizeStr));

                        totalSize += size;
                        offset += size;
                    }

                    report.AppendLine();
                    report.AppendLine("  TOTAL SIZE: " + totalSize + " bytes (0x" + totalSize.ToString("X") + ")");
                    report.AppendLine();
                }
            }

            // Look for packet-related methods in wfm_progress
            Type wfmProgress = null;
            foreach (Type t in assembly.GetTypes())
            {
                if (t.Name == "wfm_progress" || (t.FullName != null && t.FullName.Contains("wfm_progress")))
                {
                    wfmProgress = t;
                    break;
                }
            }

            if (wfmProgress != null)
            {
                report.AppendLine();
                report.AppendLine("WFM_PROGRESS CLASS - DOWNLOAD METHODS");
                report.AppendLine(new string('-', 80));
                report.AppendLine();

                MethodInfo[] wfmMethods = wfmProgress.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);

                foreach (MethodInfo method in wfmMethods)
                {
                    if (method.Name.Contains("download") || method.Name.Contains("packet") ||
                        method.Name.Contains("PareUpdata") || method.Name == "Updata")
                    {
                        report.AppendLine("Method: " + method.Name);
                        report.AppendLine("  Returns: " + method.ReturnType.Name);

                        ParameterInfo[] parameters = method.GetParameters();
                        if (parameters.Length > 0)
                        {
                            report.AppendLine("  Parameters:");
                            foreach (ParameterInfo param in parameters)
                            {
                                report.AppendLine("    - " + param.ParameterType.Name + " " + param.Name);
                            }
                        }

                        // Get method body
                        try
                        {
                            System.Reflection.MethodBody body = method.GetMethodBody();
                            if (body != null)
                            {
                                report.AppendLine("  IL Code Size: " + body.GetILAsByteArray().Length + " bytes");
                                report.AppendLine("  Max Stack: " + body.MaxStackSize);

                                var locals = body.LocalVariables;
                                if (locals.Count > 0)
                                {
                                    report.AppendLine("  Local Variables:");
                                    for (int i = 0; i < locals.Count; i++)
                                    {
                                        report.AppendLine("    [" + i + "] " + locals[i].LocalType.Name);
                                    }
                                }
                            }
                        }
                        catch { }

                        report.AppendLine();
                    }
                }
            }

            // Save report
            string reportFile = "TK11_BOOTLOADER_PROTOCOL.txt";
            File.WriteAllText(reportFile, report.ToString(), Encoding.UTF8);

            Console.WriteLine("[+] Protocol documentation saved to: " + reportFile);
            Console.WriteLine();

            // Also print summary to console
            Console.WriteLine("SUMMARY");
            Console.WriteLine(new string('-', 80));
            Console.WriteLine();
            Console.WriteLine("Found " + fields.Length + " fields in protocol_struct");
            Console.WriteLine("Found " + methods.Length + " methods in protocol_struct");
            Console.WriteLine("Found " + nestedTypes.Length + " nested message structures");
            Console.WriteLine();
            Console.WriteLine("[*] Check " + reportFile + " for full details");

        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.Message);
            Console.WriteLine("Stack trace: " + ex.StackTrace);
        }
    }
}
